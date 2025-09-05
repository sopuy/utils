// telegram.go
package base

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
    "net/url"
)

type TgPayload struct {
    ChatID string `json:"chat_id"`
    Text   string `json:"text"`
}

func SendTgMsg(chatID, tgToken, content, httpsProxy string) (*http.Response, error) {
    tgBotAPISendMsg := fmt.Sprintf("https://api.telegram.org/bot%s/sendMessage", tgToken)

    payload := TgPayload{
        ChatID: chatID,
        Text:   content,
    }
    payloadBytes, err := json.Marshal(payload)
    if err != nil {
        return nil, err
    }

    req, err := http.NewRequest("POST", tgBotAPISendMsg, bytes.NewBuffer(payloadBytes))
    if err != nil {
        return nil, err
    }
    req.Header.Set("Content-Type", "application/json")

    client := &http.Client{}
    if httpsProxy != "" {
        proxyURL, err := url.Parse(httpsProxy)
        if err != nil {
            return nil, err
        }
        client.Transport = &http.Transport{Proxy: http.ProxyURL(proxyURL)}
        fmt.Println("Using proxy:", httpsProxy)
    }

    resp, err := client.Do(req)
    if err != nil {
        fmt.Println("Error sending request:", err)
        return nil, err
    }
    defer resp.Body.Close()
    return resp, nil
}