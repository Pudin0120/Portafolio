package com.prabhu.womensafetyapp;

import android.os.Bundle;
import android.app.Activity;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;
import android.support.v4.app.NavUtils;
import android.annotation.TargetApi;
import android.content.Context;
import android.content.ContentValues;
import android.content.Intent;
import android.database.sqlite.SQLiteDatabase;
import android.os.Build;

public class Verify extends Activity {

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_verify);
		// Show the Up button in the action bar.
		setupActionBar();
		
		
		
	}
	
	
    public void verify_no(View view) {
        EditText sourceNumber = findViewById(R.id.editText1);
        String phoneNumber = sourceNumber.getText().toString().trim()
                .replaceAll("[\\s()-]", "");

        if (!phoneNumber.matches("\\+?[0-9]{7,15}")) {
            sourceNumber.setError("Enter a valid phone number.");
            return;
        }

        SQLiteDatabase database = openOrCreateDatabase("NumDB", Context.MODE_PRIVATE, null);
        try {
            database.execSQL("CREATE TABLE IF NOT EXISTS source (number VARCHAR(20))");
            database.delete("source", null, null);

            ContentValues values = new ContentValues();
            values.put("number", phoneNumber);
            long savedId = database.insert("source", null, values);
            if (savedId == -1) {
                Toast.makeText(this, "Unable to save your number.", Toast.LENGTH_SHORT).show();
                return;
            }
            Toast.makeText(this, "Your number was saved.", Toast.LENGTH_SHORT).show();
            back(view);
        } finally {
            database.close();
        }
    }


	/**
	 * Set up the {@link android.app.ActionBar}, if the API is available.
	 */
	@TargetApi(Build.VERSION_CODES.HONEYCOMB)
	private void setupActionBar() {
		if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.HONEYCOMB) {
			getActionBar().setDisplayHomeAsUpEnabled(true);
		}
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.verify, menu);
		return true;
	}

	@Override
	public boolean onOptionsItemSelected(MenuItem item) {
		switch (item.getItemId()) {
		case android.R.id.home:
			// This ID represents the Home or Up button. In the case of this
			// activity, the Up button is shown. Use NavUtils to allow users
			// to navigate up one level in the application structure. For
			// more details, see the Navigation pattern on Android Design:
			//
			// http://developer.android.com/design/patterns/navigation.html#up-vs-back
			//
			NavUtils.navigateUpFromSameTask(this);
			return true;
		}
		return super.onOptionsItemSelected(item);
	}
	
	
	public void back(View v) {
		Intent i_back=new Intent(Verify.this,MainActivity.class);
		startActivity(i_back);
			
		}

}
