package com.aniketjain.weatherapp.location;

import com.aniketjain.weatherapp.BuildConfig;

public final class LocationCord {

    public static String lat = "";
    public static String lon = "";

    private LocationCord() {
    }

    public static boolean hasApiKey() {
        return BuildConfig.WEATHER_API_KEY != null
                && !BuildConfig.WEATHER_API_KEY.trim().isEmpty();
    }
}
