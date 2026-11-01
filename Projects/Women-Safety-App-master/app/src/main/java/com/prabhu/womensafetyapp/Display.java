package com.prabhu.womensafetyapp;

import android.app.Activity;
import android.app.AlertDialog.Builder;
import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.os.Bundle;
import android.view.View;

public class Display extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_display);
        showRegisteredContacts();
    }

    private void showRegisteredContacts() {
        SQLiteDatabase database = openOrCreateDatabase("NumDB", Context.MODE_PRIVATE, null);
        StringBuilder message = new StringBuilder();

        try {
            database.execSQL("CREATE TABLE IF NOT EXISTS details (name VARCHAR(80), number VARCHAR(20))");
            try (Cursor contacts = database.rawQuery(
                    "SELECT name, number FROM details ORDER BY rowid ASC", null)) {
                while (contacts.moveToNext()) {
                    message.append("Name: ").append(contacts.getString(0)).append("\n")
                            .append("Number: ").append(contacts.getString(1)).append("\n\n");
                }
            }
        } finally {
            database.close();
        }

        if (message.length() == 0) {
            showMessage("Emergency contacts", "No emergency contacts have been registered.");
        } else {
            showMessage("Registered emergency contacts", message.toString().trim());
        }

        startService(new Intent(Display.this, BgService.class));
    }

    private void showMessage(String title, String message) {
        new Builder(this)
                .setCancelable(true)
                .setTitle(title)
                .setMessage(message)
                .setPositiveButton(android.R.string.ok, null)
                .show();
    }

    public void back(View view) {
        startActivity(new Intent(Display.this, MainActivity.class));
        finish();
    }
}
