//+------------------------------------------------------------------+
//|                                              SpineDashboard.mq5 |
//|                                  Copyright 2024, Spine Miner    |
//|                                             https://spine.miner |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, Spine Miner"
#property link      "https://spine.miner"
#property version   "1.00"
#property strict
#property indicator_chart_window

//--- input parameters
input string   ServerURL = "http://localhost:5002/api/mt5";
input int      RefreshInterval = 5; // Refresh interval in seconds

//--- global variables
long           last_refresh = 0;
string         display_text = "Connecting to Spine Miner...";

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
{
   EventSetTimer(RefreshInterval);
   RefreshData();
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Custom indicator deinitialization function                       |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   EventKillTimer();
   ObjectsDeleteAll(0, "Spine_");
}

//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
{
   UpdateDisplay();
   return(rates_total);
}

//+------------------------------------------------------------------+
//| Timer function                                                   |
//+------------------------------------------------------------------+
void OnTimer()
{
   RefreshData();
   UpdateDisplay();
}

//+------------------------------------------------------------------+
//| Fetch data from the web API                                      |
//+------------------------------------------------------------------+
void RefreshData()
{
   char post[], result[];
   string headers;
   int timeout = 5000;

   int res = WebRequest("GET", ServerURL, NULL, NULL, timeout, post, 0, result, headers);

   if(res == -1)
   {
      display_text = "API Error: Check WebRequest permissions in MT5 Options (Expert Advisors)";
      Print("Error in WebRequest: ", GetLastError());
   }
   else if(res == 200)
   {
      string json_raw = CharArrayToString(result);
      display_text = "Spine Miner Unified Dashboard\n" +
                     "-----------------------------\n" +
                     json_raw;
   }
   else
   {
      display_text = "Server error: " + (string)res;
   }
}

//+------------------------------------------------------------------+
//| Display the dashboard on the chart                               |
//+------------------------------------------------------------------+
void UpdateDisplay()
{
   string name = "Spine_Dashboard_Label";
   if(ObjectFind(0, name) < 0)
   {
      ObjectCreate(0, name, OBJ_LABEL, 0, 0, 0);
      ObjectSetInteger(0, name, OBJPROP_XDISTANCE, 20);
      ObjectSetInteger(0, name, OBJPROP_YDISTANCE, 20);
      ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetString(0, name, OBJPROP_FONT, "Consolas");
      ObjectSetInteger(0, name, OBJPROP_FONTSIZE, 12);
      ObjectSetInteger(0, name, OBJPROP_COLOR, clrYellow);
   }

   ObjectSetString(0, name, OBJPROP_TEXT, display_text);
   ChartRedraw(0);
}
