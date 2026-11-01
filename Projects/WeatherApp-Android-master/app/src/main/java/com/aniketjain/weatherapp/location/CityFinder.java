package com.aniketjain.weatherapp.location;

import android.content.Context;
import android.location.Address;
import android.location.Geocoder;
import android.location.Location;

import java.io.IOException;
import java.util.List;
import java.util.Locale;

public final class CityFinder {

    private CityFinder() {
    }

    public static boolean setLongitudeLatitude(Location location) {
        if (location == null) {
            return false;
        }
        LocationCord.lat = String.valueOf(location.getLatitude());
        LocationCord.lon = String.valueOf(location.getLongitude());
        return true;
    }

    public static String getCityNameUsingNetwork(Context context, Location location) {
        if (context == null || location == null || !Geocoder.isPresent()) {
            return "";
        }

        try {
            Geocoder geocoder = new Geocoder(context, Locale.getDefault());
            List<Address> addresses = geocoder.getFromLocation(
                    location.getLatitude(), location.getLongitude(), 1);
            if (addresses == null || addresses.isEmpty()) {
                return "";
            }
            String locality = addresses.get(0).getLocality();
            return locality == null ? "" : locality;
        } catch (IOException | IllegalArgumentException exception) {
            return "";
        }
    }
}
