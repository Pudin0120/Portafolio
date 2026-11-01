package com.aniketjain.weatherapp.url;

import android.net.Uri;

import com.aniketjain.weatherapp.BuildConfig;
import com.aniketjain.weatherapp.location.LocationCord;

public class URL {

    private static final String API_BASE = "https://api.openweathermap.org/data/2.5/";

    private final String link;

    public URL() {
        link = Uri.parse(API_BASE + "onecall")
                .buildUpon()
                .appendQueryParameter("exclude", "minutely")
                .appendQueryParameter("lat", LocationCord.lat)
                .appendQueryParameter("lon", LocationCord.lon)
                .appendQueryParameter("appid", BuildConfig.WEATHER_API_KEY)
                .build()
                .toString();
    }

    public String getLink() {
        return link;
    }

    public static String getCityUrl(String cityName) {
        return Uri.parse(API_BASE + "weather")
                .buildUpon()
                .appendQueryParameter("q", cityName)
                .appendQueryParameter("appid", BuildConfig.WEATHER_API_KEY)
                .build()
                .toString();
    }
}
