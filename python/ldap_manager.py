#!/usr/bin/env python3
# coding=utf-8
###############################################################################
"""
__author__ = "sunhn"

Description:

"""

import logging
import ldap
from datetime import datetime, timedelta, timezone
from typing import Tuple
from .password_manager import check_password_complexity_with_reason
from config import CONFIG

logger = logging.getLogger(__name__)


XOPS_USERNAME = CONFIG.auth.ldap.jc_manager_uid
XOPS_PASSWORD = CONFIG.auth.ldap.jc_manager_password

JC_LDAP_SERVER_URI = CONFIG.auth.ldap.url
JC_BASE_DN = CONFIG.auth.ldap.jc_base_dn
CA_CERT_FILE = CONFIG.auth.ldap.ca_cert_path


class OpenLDAPClient:
    """
    A class for interacting with an OpenLDAP server over TLS.
    It provides functionality for user authentication, password modification,
    and password expiry time lookup.
    """

    def __init__(self, ldap_uri: str, base_dn: str, ca_cert_file: str = None):
        """
        Initializes the LDAP connection details.
        :param ldap_uri: The URI of the LDAP server, must be a TLS address starting with "ldaps://",
                         e.g., "ldaps://ldap.example.com:636"
        :param base_dn: The base Distinguished Name (DN) of the LDAP directory tree,
                        e.g., "dc=example,dc=com"
        :param ca_cert_file: (Optional) The path to the CA certificate file. Providing this
                             enables server certificate validation for enhanced security.
        """
        if not ldap_uri.startswith("ldaps://"):
            raise ValueError("LDAP URI must start with 'ldaps://' for a TLS connection.")

        self.ldap_uri = ldap_uri
        self.base_dn = base_dn
        self.ca_cert_file = ca_cert_file

    def _get_connection(self) -> ldap.ldapobject.LDAPObject:
        """
        Establishes and returns an LDAP connection object with TLS options configured.
        """
        if self.ca_cert_file:
            # Most secure option: Requires validation of the server certificate
            ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, self.ca_cert_file)
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_DEMAND)
        else:
            # WARNING: Not recommended for production. This allows connecting to any TLS endpoint
            # without verifying its identity. Use only for local testing or with self-signed
            # server certificates where the CA is not available.
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)
            logging.warning("No CA certificate file provided. Server certificate will not be verified.")

        # Set the protocol version to LDAPv3
        ldap.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3)

        conn = ldap.initialize(self.ldap_uri)
        return conn

    def _get_user_dn(self, username: str) -> str:
        """
        Constructs the full user DN based on the username.
        Assumes user entries are under "ou=people" and use "uid" as the unique identifier.
        """
        # A simple check for an admin user which might be located elsewhere
        if username == "admin":
            return f"cn=admin,{self.base_dn}"
        elif username == "xops":
            return f"uid={username},ou=service,{self.base_dn}"
        else:
            return f"uid={username},ou=people,{self.base_dn}"

    def authenticate(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Authenticates a user's password.

        :param username: The username to authenticate.
        :param password: The password to verify.
        :return: True if the password is correct, False otherwise.
        """
        user_dn = self._get_user_dn(username)
        conn = self._get_connection()

        try:
            # Attempt to bind as the user. If successful, the credentials are valid.
            conn.simple_bind_s(user_dn, password)
            msg = f"Authentication successful for user: {username}"
            logging.info(msg)
            return True, msg
        except ldap.INVALID_CREDENTIALS:
            msg = f"Authentication failed: Invalid credentials for user {username}."
            logging.warning(msg)
            return False, msg
        except ldap.SERVER_DOWN as e:
            msg = f"LDAP server is down or unreachable: {e}"
            logging.error(msg)
            return False, msg
        except ldap.LDAPError as e:
            msg = f"An LDAP error occurred during authentication for {username}: {e}"
            logging.error(msg)
            return False, msg
        finally:
            # Ensure the connection is closed
            conn.unbind_s()

    def change_password(self, username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
        """
        Changes a user's password.

        :param username: The username whose password to change.
        :param old_password: The user's old password.
        :param new_password: The user's new password.
        :return: A tuple (bool, str) indicating success and a message.
        """
        user_dn = self._get_user_dn(username)
        conn = self._get_connection()

        try:
            # First, bind with the old password to prove authorization
            conn.simple_bind_s(user_dn, old_password)
            logger.info("Bind successful with old password")
            check_status, check_msg = check_password_complexity_with_reason(new_password)
            logger.info(f"Check password complexity: {check_msg}")
            if not check_status:
                logger.error(f"Password complexity check failed: {check_msg}")
                return False, check_msg
            # Use the LDAP password modify extended operation
            conn.passwd_s(user_dn, old_password.encode("utf-8"), new_password.encode("utf-8"))

            logging.info(f"Password changed successfully for user: {username}")
            return True, "Password changed successfully."
        except ldap.INVALID_CREDENTIALS:
            logging.warning(f"Password change failed for {username}: Invalid old password.")
            return False, "Invalid old password."
        except ldap.UNWILLING_TO_PERFORM as e:
            # Usually indicates that the new password does not meet the server's policy
            logging.error(f"Password change failed for {username}: Password does not meet policy. Server says: {e}")
            return False, "New password does not meet the complexity/history policy."
        except ldap.SERVER_DOWN as e:
            logging.error(f"LDAP server is down or unreachable: {e}")
            return False, "LDAP server is unavailable."
        except ldap.LDAPError as e:
            logging.error(f"An LDAP error occurred during password change for {username}: {e}")
            return False, f"An LDAP error occurred: {e}"
        finally:
            conn.unbind_s()

    def get_user_info(
        self, username_to_query: str, admin_user: str = XOPS_USERNAME, admin_password: str = XOPS_PASSWORD
    ) -> dict:
        """
        查询 LDAP 用户的基本信息。

        :param username_to_query: 需要查询的用户名
        :param admin_user: 管理员用户名，用于有权限查询时
        :param admin_password: 管理员密码
        :return: 字典形式的用户信息，找不到用户时返回 message
        """
        # 使用管理员绑定还是自己绑定
        bind_user = admin_user or username_to_query
        bind_password = admin_password or ""  # 如果查询自己，密码必须传

        user_dn = self._get_user_dn(bind_user)
        conn = self._get_connection()

        try:
            # 绑定
            conn.simple_bind_s(user_dn, bind_password)

            # 搜索用户条目
            search_filter = f"(uid={username_to_query})"
            # 查询常用属性，可根据实际 LDAP schema 增加
            search_attributes = ["uid", "cn", "mail", "displayName", "sn", "givenName", "ou"]

            result = conn.search_s(self.base_dn, ldap.SCOPE_SUBTREE, search_filter, search_attributes)

            if not result:
                return {"message": f"User '{username_to_query}' not found."}

            user_entry = result[0][1]

            # 将 bytes 转为 str
            user_info = {k: v[0].decode("utf-8") if isinstance(v[0], bytes) else v[0] for k, v in user_entry.items()}

            return user_info

        except ldap.INVALID_CREDENTIALS:
            msg = f"Invalid credentials for user '{bind_user}'."
            logging.error(msg)
            return {"message": msg}
        except ldap.LDAPError as e:
            msg = f"LDAP error occurred while querying '{username_to_query}': {e}"
            logging.error(msg)
            return {"message": msg}
        finally:
            conn.unbind_s()

    def get_password_expiry_info(
        self, username_to_query: str, admin_user: str = XOPS_USERNAME, admin_password: str = XOPS_PASSWORD
    ) -> dict:
        """
        Queries the password expiry information for a specified user.
        Requires administrator privileges to read password policy operational attributes.

        This functionality requires the OpenLDAP server to have the ppolicy (Password Policy)
        overlay enabled.

        :param admin_user: An administrator username with rights to read operational attributes.
        :param admin_password: The administrator's password.
        :param username_to_query: The username of the user whose password expiry information is to be queried.
        :return: A dictionary containing expiry information, e.g.,
                 {'expiry_date': datetime_obj, 'days_left': 10, 'message': '...'}
                 or a message if the password never expires or information cannot be retrieved.
        """
        admin_dn = self._get_user_dn(admin_user)
        conn = self._get_connection()

        try:
            # Bind as the administrator to gain necessary permissions
            conn.simple_bind_s(admin_dn, admin_password)

            # Query the user's password policy-related attributes
            # We need to search for the user and request operational attributes '+' or specific ones like 'pwdChangedTime'
            search_filter = f"(uid={username_to_query})"
            search_attributes = ["pwdChangedTime", "pwdPolicySubentry"]

            # The search must be performed on the base_dn
            result = conn.search_s(self.base_dn, ldap.SCOPE_SUBTREE, search_filter, search_attributes)

            if not result:
                return {"message": f"User '{username_to_query}' not found."}

            user_entry = result[0][1]

            if "pwdChangedTime" not in user_entry:
                return {"message": "Could not retrieve password last changed time. ppolicy overlay may not be active."}

            # Parse the last password change time
            changed_time_str = user_entry["pwdChangedTime"][0].decode("utf-8").rstrip("Z")
            pwd_changed_time = datetime.strptime(changed_time_str, "%Y%m%d%H%M%S")

            # Get the password policy
            if "pwdPolicySubentry" not in user_entry:
                return {"message": "User is not subject to any password policy."}

            policy_dn = user_entry["pwdPolicySubentry"][0].decode("utf-8")

            # Query the policy itself to get pwdMaxAge
            policy_result = conn.search_s(policy_dn, ldap.SCOPE_BASE, attrlist=["pwdMaxAge"])

            if not policy_result or "pwdMaxAge" not in policy_result[0][1]:
                return {"message": "Could not retrieve pwdMaxAge from the password policy."}

            pwd_max_age_seconds = int(policy_result[0][1]["pwdMaxAge"][0])

            if pwd_max_age_seconds == 0:
                return {"expiry_date": None, "days_left": float("inf"), "message": "Password is set to never expire."}

            # Calculate the expiry date
            expiry_date_naive = pwd_changed_time + timedelta(seconds=pwd_max_age_seconds)
            expiry_date_aware = expiry_date_naive.replace(tzinfo=timezone.utc)
            now_utc = datetime.now(timezone.utc)

            days_left = (expiry_date_aware - now_utc).days
            return {
                "expiry_date": expiry_date_aware,
                "days_left": days_left,
                "last_changed": pwd_changed_time,
                "message": f"Password expires on {expiry_date_aware.isoformat()} UTC.",
            }

        except ldap.INSUFFICIENT_ACCESS:
            msg = f"Admin user '{admin_user}' does not have sufficient rights to read password policy attributes."
            logging.error(msg)
            return {"message": msg}
        except ldap.NO_SUCH_OBJECT:
            msg = f"User '{username_to_query}' or required policy object not found."
            logging.error(msg)
            return {"message": msg}
        except ldap.LDAPError as e:
            logging.error(f"An LDAP error occurred while querying expiry for {username_to_query}: {e}")
            return {"message": f"An LDAP error occurred: {e}"}
        finally:
            conn.unbind_s()


ldap_client = OpenLDAPClient(ldap_uri=JC_LDAP_SERVER_URI, base_dn=JC_BASE_DN)

if __name__ == "__main__":
    LOG_HANDLERS = [
        # logging.FileHandler(f"{__file__}.log", encoding="utf-8"),
        logging.StreamHandler(),
    ]
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s [%(filename)s:%(lineno)d] - %(message)s",
        level=logging.INFO,
        handlers=LOG_HANDLERS,
    )
    TEST_USERNAME = "test"
    is_valid = ldap_client.authenticate(username=XOPS_USERNAME, password=XOPS_PASSWORD)
    logger.info(f"Authentication for {TEST_USERNAME} is {is_valid}")
    data = ldap_client.get_user_info(username_to_query=TEST_USERNAME)
    info = ldap_client.get_password_expiry_info(TEST_USERNAME)
    ret = {**data, **info}
    logger.info(f"Password expiry info for {TEST_USERNAME} is {ret}")

    # ldap_client.change_password(TEST_USERNAME, TEST_PASSWORD, "123")
