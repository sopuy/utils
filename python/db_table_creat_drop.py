#!/usr/bin/env python3
# coding=utf-8
###############################################################################
"""
__author__ = "sunhn"

Description:
    create table for fastapi

models.py __all__=[all_models]
"""

import logging
import sys
import asyncio
import argparse

sys.path.append("..")
from config import CONFIG

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s [%(filename)s:%(lineno)d] - %(message)s",
    handlers=([logging.StreamHandler()]),
)


def manage_table_sync(engine, model, table: str, act="create"):
    if act == "create":
        # third_models.ThirdWxToken.__table__.drop(db_engine)
        getattr(model, table).__table__.create(engine)
    elif act == "drop":
        getattr(model, table).__table__.drop(engine)


async def table_exists(engine, table_name):
    async with engine.begin() as conn:
        result = await conn.run_sync(lambda conn: conn.dialect.has_table(conn, table_name))
    return result


async def drop_table(engine, table):
    async with engine.begin() as conn:
        await conn.run_sync(table.drop)


async def create_table(engine, table):
    async with engine.begin() as conn:
        await conn.run_sync(table.create)


async def main(engine, models):
    for model in getattr(models, "__all__"):
        table = getattr(getattr(models, model), "__table__")
        logger.info(f"start process {table}")
        if await table_exists(engine, getattr(table, "name")):
            if CONFIG.app.env == "dev":
                logger.info(f"Table {table} exists. Dropping and recreating.")
                await drop_table(engine, table)
                logger.info(f"Table {table} has been dropped.")
                await create_table(engine, table)
                logger.info(f"Table {table} has been created.")
            else:
                logger.info(f"Table {table} exists. Skipping.")
        else:
            logger.info(f"Table {table} does not exist. Creating.")
            await create_table(engine, table)
            logger.info(f"Table {table} has been created.")


if __name__ == "__main__":
    model_list = ["auth", "core", "cmdb", "third", "task", "findata"]
    model_list_all = model_list + ["all"]

    parser = argparse.ArgumentParser(description="Create or drop database tables.")
    parser.add_argument("model", choices=model_list_all, help="Specify the model to create/drop tables for.")
    args = parser.parse_args()

    sys.path.append("../")
    from core.db_manager import db_manager
    from core import models as core_models
    from apps.cmdb import models as cmdb_models
    from apps.auth import models as auth_models
    from apps.third import models as third_models
    from apps.task import models as task_models
    from apps.findata import models as findata_models

    asyncio.run(db_manager.connect())
    _engine = db_manager._engine

    if args.model == "all":
        for model_name in model_list:
            models = eval(f"{model_name}_models")
            asyncio.run(main(_engine, models))
            logger.info(f"Table created successfully for {model_name}")
    else:
        models = eval(f"{args.model}_models")
        asyncio.run(main(_engine, models))
        logger.info(f"Table created successfully for {args.model}")
