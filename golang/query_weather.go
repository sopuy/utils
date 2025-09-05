/*
This demand is derived due to Apple's inaccurate weather conditions.

geocode api
https://lbs.amap.com/api/webservice/guide/api/georegeo

dongcheng 110101
xicheng   110102
haidian   110108
changping 110114
chaoyang  110105
fengtai   110106

https://lbs.amap.com/api/webservice/guide/api/weatherinfo

https://restapi.amap.com/v3/weather/weatherInfo?city={citycode}&key={key}
*/
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"time"

	"ace.com/src/base"
)

func getWeatherData(url string) (map[string]interface{}, error) {
    resp, err := http.Get(url)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("failed to fetch data: %s", resp.Status)
    }

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, err
    }

    var result map[string]interface{}
    if err := json.Unmarshal(body, &result); err != nil {
        return nil, err
    }

    return result, nil
}


func formatWeatherData(data map[string]interface{}) string {
    now := time.Now()
    var result string
    // 处理实时天气数据
    if data["status"] == "1" {
        if lives, ok := data["lives"].([]interface{}); ok && len(lives) > 0 {
            live := lives[0].(map[string]interface{})
            result += fmt.Sprintf("实况天气-查询时间: %s\n", now.Format("2006-01-02 15:04:05"))
            result += fmt.Sprintf("城市: %s - %s\n", live["province"], live["city"])
            result += fmt.Sprintf("报告时间: %s\n", live["reporttime"])
            result += fmt.Sprintf("\n")
            result += fmt.Sprintf("天气: %s\n", live["weather"])
            result += fmt.Sprintf("温度: %s°C\n", live["temperature"])
            result += fmt.Sprintf("湿度: %s%%\n", live["humidity"])
            result += fmt.Sprintf("风向: %s\n", live["winddirection"])
            result += fmt.Sprintf("风力: %s\n", live["windpower"])
        }
    }

    // 处理天气预报数据
    if forecasts, ok := data["forecasts"].([]interface{}); ok && len(forecasts) > 0 {
        forecast := forecasts[0].(map[string]interface{})
        result += fmt.Sprintf("预报天气-查询时间: %s\n", now.Format("2006-01-02 15:04:05"))
        result += fmt.Sprintf("城市: %s-%s\n", forecast["province"], forecast["city"])
        result += fmt.Sprintf("报告时间: %s\n", forecast["reporttime"])
        result += fmt.Sprintf("\n")
        for _, cast := range forecast["casts"].([]interface{}) {
            day := cast.(map[string]interface{})
            result += fmt.Sprintf("日期: %s\n 白天气温: %s°C, 夜间气温: %s°C\n 白天天气: %s, 夜间天气: %s\n 白天风力: %s, 夜间风力 %s\n",
                day["date"], day["daytemp"], day["nighttemp"], day["dayweather"], day["nightweather"], day["daypower"], day["nightpower"])
            result += fmt.Sprintf("\n")
        }
    }
    
    return result
}


func main() {
    // 定义命令行参数
    action := flag.String("action", "live", "Specify 'live' or 'forecast'")
    cityCode := flag.String("citycode", "110105", "City code to fetch weather data")
    flag.Parse()

    apiKey := base.AmapApiKey
    baseURL := fmt.Sprintf("https://restapi.amap.com/v3/weather/weatherInfo?key=%s",apiKey)


    var url string
    if *action == "live" {
        url = fmt.Sprintf("%s&city=%s", baseURL, *cityCode)
    } else if *action == "forecast" {
        url = fmt.Sprintf("%s&city=%s&extensions=all", baseURL, *cityCode)
    } else {
        fmt.Println("Invalid action. Use 'live' or 'forecast'.")
        return
    }

    // 获取天气数据
    weatherData, err := getWeatherData(url)
    if err != nil {
        fmt.Println("Error fetching data:", err)
        return
    }

    // 打印数据
    // fmt.Println(weatherData)
    output := formatWeatherData(weatherData)
    fmt.Println(output)
    chatID := base.TgChatID
    tgToken := base.TgToken
    // httpsProxy := "http://localhost:32000"
    httpsProxy := ""
    _, err = base.SendTgMsg(chatID, tgToken, output, httpsProxy)
    if err != nil {
        fmt.Println("Error sending message:", err)
        return
    }
    fmt.Println("tg Message sent successfully!")

}
