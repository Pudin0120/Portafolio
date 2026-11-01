package com.aniketjain.weatherapp;

import static com.aniketjain.weatherapp.location.CityFinder.getCityNameUsingNetwork;
import static com.aniketjain.weatherapp.location.CityFinder.setLongitudeLatitude;
import static com.aniketjain.weatherapp.network.InternetConnectivity.isInternetConnected;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Intent;
import android.content.IntentSender;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.speech.RecognizerIntent;
import android.util.Log;
import android.view.View;
import android.view.inputmethod.EditorInfo;
import android.view.inputmethod.InputMethodManager;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.recyclerview.widget.LinearLayoutManager;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import com.aniketjain.weatherapp.adapter.DaysAdapter;
import com.aniketjain.weatherapp.databinding.ActivityHomeBinding;
import com.aniketjain.weatherapp.location.LocationCord;
import com.aniketjain.weatherapp.toast.Toaster;
import com.aniketjain.weatherapp.update.UpdateUI;
import com.aniketjain.weatherapp.url.URL;
import com.google.android.gms.location.FusedLocationProviderClient;
import com.google.android.gms.location.LocationServices;
import com.google.android.play.core.appupdate.AppUpdateInfo;
import com.google.android.play.core.appupdate.AppUpdateManager;
import com.google.android.play.core.appupdate.AppUpdateManagerFactory;
import com.google.android.play.core.install.model.AppUpdateType;
import com.google.android.play.core.install.model.UpdateAvailability;
import com.google.android.play.core.tasks.Task;

import org.json.JSONException;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.Locale;
import java.util.Objects;

public class HomeActivity extends AppCompatActivity {

    private final int WEATHER_FORECAST_APP_UPDATE_REQ_CODE = 101;   // for app update
    private static final int PERMISSION_CODE = 1;                   // for user location permission
    private String name, updated_at, description, temperature, min_temperature, max_temperature, pressure, wind_speed, humidity;
    private int condition;
    private long update_time, sunset, sunrise;
    private String city = "";
    private final int REQUEST_CODE_EXTRA_INPUT = 101;
    private ActivityHomeBinding binding;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // binding
        binding = ActivityHomeBinding.inflate(getLayoutInflater());
        View view = binding.getRoot();
        setContentView(view);

        // set navigation bar color
        setNavigationBarColor();

        //check for new app update
        checkUpdate();

        // set refresh color schemes
        setRefreshLayoutColor();

        // when user do search and refresh
        listeners();


    }


    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_CODE_EXTRA_INPUT) {
            if (resultCode == RESULT_OK && data != null) {
                ArrayList<String> results = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
                if (results != null && !results.isEmpty() && results.get(0) != null) {
                    binding.layout.cityEt.setText(results.get(0));
                    searchCity(results.get(0));
                }
            }
        }
    }


    private void setNavigationBarColor() {
        if (android.os.Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            getWindow().setNavigationBarColor(getResources().getColor(R.color.navBarColor));
        }
    }

    private void setUpDaysRecyclerView(org.json.JSONArray dailyForecast, long currentTime) {
        DaysAdapter daysAdapter = new DaysAdapter(this, dailyForecast, currentTime);
        binding.dayRv.setLayoutManager(
                new LinearLayoutManager(this, LinearLayoutManager.HORIZONTAL, false)
        );
        binding.dayRv.setAdapter(daysAdapter);
    }

    @SuppressLint("ClickableViewAccessibility")
    private void listeners() {
        binding.layout.mainLayout.setOnTouchListener((view, motionEvent) -> {
            hideKeyboard(view);
            return false;
        });
        binding.layout.searchBarIv.setOnClickListener(view -> searchCity(binding.layout.cityEt.getText().toString()));
        binding.layout.searchBarIv.setOnTouchListener((view, motionEvent) -> {
            hideKeyboard(view);
            return false;
        });
        binding.layout.cityEt.setOnEditorActionListener((textView, i, keyEvent) -> {
            if (i == EditorInfo.IME_ACTION_GO) {
                searchCity(binding.layout.cityEt.getText().toString());
                hideKeyboard(textView);
                return true;
            }
            return false;
        });
        binding.layout.cityEt.setOnFocusChangeListener((view, b) -> {
            if (!b) {
                hideKeyboard(view);
            }
        });
        binding.mainRefreshLayout.setOnRefreshListener(() -> {
            checkConnection();
            Log.i("refresh", "Refresh Done.");
            binding.mainRefreshLayout.setRefreshing(false);  //for the next time
        });
        //Mic Search
        binding.layout.micSearchId.setOnClickListener(view -> {
            Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault().toLanguageTag());
            intent.putExtra(RecognizerIntent.EXTRA_PROMPT, "Speak a city name");
            try {
                //it was deprecated but still work
                startActivityForResult(intent, REQUEST_CODE_EXTRA_INPUT);
            } catch (Exception e) {
                Log.d("Error Voice", "Mic Error:  " + e);
            }
        });
    }

    private void setRefreshLayoutColor() {
        binding.mainRefreshLayout.setProgressBackgroundColorSchemeColor(
                getResources().getColor(R.color.textColor)
        );
        binding.mainRefreshLayout.setColorSchemeColors(
                getResources().getColor(R.color.navBarColor)
        );
    }

    private void searchCity(String cityName) {
        if (cityName == null || cityName.trim().isEmpty()) {
            Toaster.errorToast(this, "Please enter the city name");
        } else {
            setLatitudeLongitudeUsingCity(cityName);
        }
    }

    private void getDataUsingNetwork() {
        if (!LocationCord.hasApiKey()) {
            hideProgressBar();
            Toaster.errorToast(this, "Configure WEATHER_API_KEY in local Gradle properties or the environment.");
            return;
        }
        FusedLocationProviderClient client = LocationServices.getFusedLocationProviderClient(this);
        //check permission
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED && ActivityCompat.checkSelfPermission(this,
                Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION}, PERMISSION_CODE);
        } else {
            client.getLastLocation().addOnSuccessListener(location -> {
                if (!setLongitudeLatitude(location)) {
                    hideProgressBar();
                    Toaster.errorToast(this, "Location is unavailable. Search for a city instead.");
                    return;
                }
                city = getCityNameUsingNetwork(this, location);
                getTodayWeatherInfo(city == null || city.trim().isEmpty() ? "Your location" : city);
            }).addOnFailureListener(error -> {
                hideProgressBar();
                Toaster.errorToast(this, "Unable to read your location. Search for a city instead.");
            });
        }
    }

    private void setLatitudeLongitudeUsingCity(String cityName) {
        if (!LocationCord.hasApiKey()) {
            Toaster.errorToast(this, "Weather service is not configured.");
            return;
        }
        RequestQueue requestQueue = Volley.newRequestQueue(HomeActivity.this);
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.GET, URL.getCityUrl(cityName), null, response -> {
            try {
                LocationCord.lat = response.getJSONObject("coord").getString("lat");
                LocationCord.lon = response.getJSONObject("coord").getString("lon");
                getTodayWeatherInfo(cityName);
                // After the successfully city search the cityEt(editText) is Empty.
                binding.layout.cityEt.setText("");
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }, error -> Toaster.errorToast(this, "Please enter the correct city name"));
        requestQueue.add(jsonObjectRequest);
    }

    @SuppressLint("DefaultLocale")
    private void getTodayWeatherInfo(String name) {
        if (!LocationCord.hasApiKey()) {
            hideProgressBar();
            Toaster.errorToast(this, "Weather service is not configured.");
            return;
        }
        URL url = new URL();
        RequestQueue requestQueue = Volley.newRequestQueue(this);
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.GET, url.getLink(), null, response -> {
            try {
                this.name = name;
                update_time = response.getJSONObject("current").getLong("dt");
                updated_at = new SimpleDateFormat("EEEE hh:mm a", Locale.ENGLISH).format(new Date(update_time * 1000));

                condition = response.getJSONArray("daily").getJSONObject(0).getJSONArray("weather").getJSONObject(0).getInt("id");
                sunrise = response.getJSONArray("daily").getJSONObject(0).getLong("sunrise");
                sunset = response.getJSONArray("daily").getJSONObject(0).getLong("sunset");
                description = response.getJSONObject("current").getJSONArray("weather").getJSONObject(0).getString("main");

                temperature = String.valueOf(Math.round(response.getJSONObject("current").getDouble("temp")));
                min_temperature = String.format("%.0f", response.getJSONArray("daily").getJSONObject(0).getJSONObject("temp").getDouble("min"));
                max_temperature = String.format("%.0f", response.getJSONArray("daily").getJSONObject(0).getJSONObject("temp").getDouble("max"));
                pressure = response.getJSONArray("daily").getJSONObject(0).getString("pressure");
                wind_speed = String.format(Locale.getDefault(), "%.0f", response.getJSONArray("daily").getJSONObject(0).getDouble("wind_speed") * 3.6);
                humidity = response.getJSONArray("daily").getJSONObject(0).getString("humidity");

                updateUI();
                hideProgressBar();
                setUpDaysRecyclerView(response.getJSONArray("daily"), update_time);
            } catch (JSONException e) {
                hideProgressBar();
                Toaster.errorToast(this, "Weather data could not be read.");
                Log.e("weather", "Invalid weather response.", e);
            }
        }, error -> {
            hideProgressBar();
            Toaster.errorToast(this, "Unable to load weather data. Please try again.");
            Log.e("weather", "Weather request failed.", error);
        });
        requestQueue.add(jsonObjectRequest);
        Log.i("weather", "Forecast request submitted.");
    }

    @SuppressLint("SetTextI18n")
    private void updateUI() {
        binding.layout.nameTv.setText(name);
        updated_at = translate(updated_at);
        binding.layout.updatedAtTv.setText(updated_at);
        binding.layout.conditionIv.setImageResource(
                getResources().getIdentifier(
                        UpdateUI.getIconID(condition, update_time, sunrise, sunset),
                        "drawable",
                        getPackageName()
                ));
        binding.layout.conditionDescTv.setText(description);
        binding.layout.tempTv.setText(temperature + " °C");
        binding.layout.minTempTv.setText(min_temperature + " °C");
        binding.layout.maxTempTv.setText(max_temperature + " °C");
        binding.layout.pressureTv.setText(pressure + " mb");
        binding.layout.windTv.setText(wind_speed + " km/h");
        binding.layout.humidityTv.setText(humidity + "%");
    }

    private String translate(String dayToTranslate) {
        String[] dayToTranslateSplit = dayToTranslate.split(" ");
        dayToTranslateSplit[0] = UpdateUI.TranslateDay(dayToTranslateSplit[0].trim(), getApplicationContext());
        return dayToTranslateSplit[0].concat(" " + dayToTranslateSplit[1]);
    }

    private void hideProgressBar() {
        binding.progress.setVisibility(View.GONE);
        binding.layout.mainLayout.setVisibility(View.VISIBLE);
    }

    private void hideMainLayout() {
        binding.progress.setVisibility(View.VISIBLE);
        binding.layout.mainLayout.setVisibility(View.GONE);
    }

    private void hideKeyboard(View view) {
        InputMethodManager inputMethodManager = (InputMethodManager) view.getContext().getSystemService(Activity.INPUT_METHOD_SERVICE);
        inputMethodManager.hideSoftInputFromWindow(view.getWindowToken(), 0);
    }

    private void checkConnection() {
        if (!isInternetConnected(this)) {
            hideMainLayout();
            Toaster.errorToast(this, "Please check your internet connection");
        } else {
            hideProgressBar();
            getDataUsingNetwork();
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PERMISSION_CODE) {
            boolean granted = false;
            for (int result : grantResults) {
                granted = granted || result == PackageManager.PERMISSION_GRANTED;
            }
            if (granted) {
                Toaster.successToast(this, "Permission Granted");
                getDataUsingNetwork();
            } else {
                Toaster.errorToast(this, "Location permission denied. You can still search for a city.");
            }
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        checkConnection();
    }

    private void checkUpdate() {
        AppUpdateManager appUpdateManager = AppUpdateManagerFactory.create(HomeActivity.this);
        Task<AppUpdateInfo> appUpdateInfoTask = appUpdateManager.getAppUpdateInfo();
        appUpdateInfoTask.addOnSuccessListener(appUpdateInfo -> {
            if (appUpdateInfo.updateAvailability() == UpdateAvailability.UPDATE_AVAILABLE
                    && appUpdateInfo.isUpdateTypeAllowed(AppUpdateType.IMMEDIATE)) {
                try {
                    appUpdateManager.startUpdateFlowForResult(appUpdateInfo, AppUpdateType.IMMEDIATE, HomeActivity.this, WEATHER_FORECAST_APP_UPDATE_REQ_CODE);
                } catch (IntentSender.SendIntentException exception) {
                    Toaster.errorToast(this, "Update Failed");
                }
            }
        });
    }

}