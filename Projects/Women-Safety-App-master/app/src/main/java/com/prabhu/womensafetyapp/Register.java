package com.prabhu.womensafetyapp;

import android.app.Activity;
import android.content.ContentValues;
import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.os.Bundle;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;

public class Register extends Activity {

    private EditText name;
    private EditText number;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_register);
    }

    public void display(View view) {
        startActivity(new Intent(Register.this, Display.class));
    }

    public void instructions(View view) {
        startActivity(new Intent(Register.this, Instructions.class));
    }

    public void storeInDB(View view) {
        name = findViewById(R.id.editText1);
        number = findViewById(R.id.editText2);

        String contactName = name.getText().toString().trim();
        String phoneNumber = normalizePhone(number.getText().toString());

        if (contactName.isEmpty() || contactName.length() > 80) {
            name.setError("Enter a name (maximum 80 characters).");
            return;
        }
        if (!phoneNumber.matches("\\+?[0-9]{7,15}")) {
            number.setError("Enter a valid phone number.");
            return;
        }

        SQLiteDatabase database = openOrCreateDatabase("NumDB", Context.MODE_PRIVATE, null);
        try {
            database.execSQL("CREATE TABLE IF NOT EXISTS details (name VARCHAR(80), number VARCHAR(20))");

            Cursor contacts = database.rawQuery("SELECT COUNT(*) FROM details", null);
            int contactCount = 0;
            try {
                if (contacts.moveToFirst()) {
                    contactCount = contacts.getInt(0);
                }
            } finally {
                contacts.close();
            }

            if (contactCount >= 2) {
                database.execSQL(
                        "DELETE FROM details WHERE rowid = (SELECT rowid FROM details ORDER BY rowid ASC LIMIT 1)");
            }

            ContentValues values = new ContentValues();
            values.put("name", contactName);
            values.put("number", phoneNumber);
            long insertedId = database.insert("details", null, values);

            if (insertedId == -1) {
                Toast.makeText(this, "Unable to save this contact.", Toast.LENGTH_SHORT).show();
            } else {
                Toast.makeText(this, "Emergency contact saved.", Toast.LENGTH_SHORT).show();
                name.setText("");
                number.setText("");
            }
        } finally {
            database.close();
        }
    }

    private String normalizePhone(String value) {
        if (value == null) {
            return "";
        }
        return value.trim().replaceAll("[\\s()-]", "");
    }
}
