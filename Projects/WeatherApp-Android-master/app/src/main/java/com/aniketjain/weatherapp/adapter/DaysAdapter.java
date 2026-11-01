package com.aniketjain.weatherapp.adapter;

import android.annotation.SuppressLint;
import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.RelativeLayout;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.aniketjain.weatherapp.R;
import com.aniketjain.weatherapp.update.UpdateUI;
import com.github.ybq.android.spinkit.SpinKitView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;

public class DaysAdapter extends RecyclerView.Adapter<DaysAdapter.DayViewHolder> {

    private final Context context;
    private final JSONArray dailyForecast;
    private final long currentTime;

    public DaysAdapter(Context context, JSONArray dailyForecast, long currentTime) {
        this.context = context;
        this.dailyForecast = dailyForecast;
        this.currentTime = currentTime;
    }

    @NonNull
    @Override
    public DayViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(context).inflate(R.layout.day_item_layout, parent, false);
        return new DayViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull DayViewHolder holder, int position) {
        bindForecast(holder, position + 1);
    }

    @Override
    public int getItemCount() {
        return dailyForecast == null ? 0 : Math.min(6, Math.max(0, dailyForecast.length() - 1));
    }

    @SuppressLint("SetTextI18n")
    private void bindForecast(DayViewHolder holder, int dayIndex) {
        try {
            JSONObject day = dailyForecast.getJSONObject(dayIndex);
            JSONObject weather = day.getJSONArray("weather").getJSONObject(0);
            JSONObject temperature = day.getJSONObject("temp");

            long sunrise = day.getLong("sunrise");
            long sunset = day.getLong("sunset");
            int condition = weather.getInt("id");
            String description = weather.optString("main", "");

            Calendar calendar = Calendar.getInstance();
            calendar.setTimeInMillis(currentTime * 1000L);
            calendar.add(Calendar.DAY_OF_YEAR, dayIndex);
            String dayName = new SimpleDateFormat("EEEE", Locale.ENGLISH)
                    .format(new Date(calendar.getTimeInMillis()));

            holder.dTime.setText(UpdateUI.TranslateDay(dayName, context));
            holder.temp_min.setText(Math.round(temperature.getDouble("min")) + " °C");
            holder.temp_max.setText(Math.round(temperature.getDouble("max")) + " °C");
            holder.pressure.setText(day.optString("pressure", "--") + " mb");
            holder.wind.setText(Math.round(day.optDouble("wind_speed", 0) * 3.6) + " km/h");
            holder.humidity.setText(day.optString("humidity", "--") + "%");

            int iconId = context.getResources().getIdentifier(
                    UpdateUI.getIconID(condition, currentTime + (dayIndex * 86400L), sunrise, sunset),
                    "drawable",
                    context.getPackageName());
            if (iconId != 0) {
                holder.icon.setImageResource(iconId);
            }
            holder.progress.setVisibility(View.GONE);
            holder.layout.setVisibility(View.VISIBLE);
        } catch (JSONException | RuntimeException exception) {
            holder.progress.setVisibility(View.GONE);
            holder.layout.setVisibility(View.VISIBLE);
            holder.dTime.setText(context.getString(R.string.forecast_unavailable));
            holder.temp_min.setText("--");
            holder.temp_max.setText("--");
            holder.pressure.setText("--");
            holder.wind.setText("--");
            holder.humidity.setText("--");
        }
    }

    static class DayViewHolder extends RecyclerView.ViewHolder {
        final SpinKitView progress;
        final RelativeLayout layout;
        final TextView dTime, temp_min, temp_max, pressure, wind, humidity;
        final ImageView icon;

        DayViewHolder(@NonNull View itemView) {
            super(itemView);
            progress = itemView.findViewById(R.id.day_progress_bar);
            layout = itemView.findViewById(R.id.day_relative_layout);
            dTime = itemView.findViewById(R.id.day_time);
            temp_min = itemView.findViewById(R.id.day_min_temp);
            temp_max = itemView.findViewById(R.id.day_max_temp);
            pressure = itemView.findViewById(R.id.day_pressure);
            wind = itemView.findViewById(R.id.day_wind);
            humidity = itemView.findViewById(R.id.day_humidity);
            icon = itemView.findViewById(R.id.day_icon);
        }
    }
}
