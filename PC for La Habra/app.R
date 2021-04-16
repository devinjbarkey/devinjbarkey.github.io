#Covid Tracker App for La Habra

library(shiny)
library(tidyverse)
library(httr)
library(jsonlite)
library(ggplot2)
library(dplyr)
library(plotly)

ui <- fluidPage(
  plotlyOutput("cases"),
  plotlyOutput("cum")
)

server <- function(input, output) {
  
  path <- "https://services2.arcgis.com/LORzk2hk9xzHouw9/arcgis/rest/services/Public_OC_COVID_Cases_by_City_by_Day/FeatureServer/0/query?where=1%3D1&outFields=La_Habra,DateSpecCollect&outSR=4326&f=json"
  request <- GET(url = path)
  response <- content(request, as = "text")
  df <- fromJSON(response, flatten = TRUE)
  
  data <- df$features
  data <- rename(data, date = attributes.DateSpecCollect, cases = attributes.La_Habra)
  data$date <- as.Date(data$date, format = '%d-%b-%y')
  data <- filter(data, date >= as.Date("2020-03-01"))
  data <- data[order(data$date),]
  data$cum_cases <- cumsum(data$cases)
  
  output$cases <- renderPlotly({
    p1 <- ggplot(data, aes(x = date, y = cases)) + geom_area(fill = 'red') + labs(x = 'Date', y = 'Cases', title = "Daily Reported COVID-19 Cases in La Habra")
    ggplotly(p1)
  })
  
  output$cum <- renderPlotly({
    p2 <- ggplot(data, aes(x = date, y = cum_cases)) + geom_area(fill = 'red') + labs(x = 'Date', y = 'Cumulative Cases', title = "Cumulative Reported COVID-19 Cases in La Habra")
    ggplotly(p2)
  })
}

shinyApp(ui = ui, server = server)
