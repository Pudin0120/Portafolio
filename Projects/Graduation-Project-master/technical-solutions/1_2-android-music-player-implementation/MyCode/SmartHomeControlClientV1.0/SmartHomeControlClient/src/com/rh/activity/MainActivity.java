package com.rh.activity;



import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.app.Activity;
import android.content.Intent;

/**
 * @Title:		
 * @Fution:		
 * @Author: 	rh_Jameson
 * @date:		2014/10/24
 */

//
class WhatMessage{
	public static final int gotoLoginActivity=0;	
}


public class MainActivity extends Activity {
	Handler handler;
	
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        //setContentView(R.layout.activity_main);
        
		/////////////////////////////////////////
		//
		handler=new Handler(){		
			@Override
			public void handleMessage(Message msg) {
			// TODO Auto-generated method stub		
				switch(msg.what){
					case WhatMessage.gotoLoginActivity:
					gotoLoginActivity();
					break;
							
				}
			}
		};
		
		///////////////////////////////////////////////	
		//
		WelcomeView welcomView=new WelcomeView(this);		
		setContentView(welcomView);
	        
    }
    
    //Activity
  	private void gotoLoginActivity() {
  		// TODO Auto-generated method stub
  		Intent intent=new Intent();
  		intent.setClass(MainActivity.this,LoginActivity.class);
  		
  		startActivity(intent);
  	}


  	//
  	public void sendMessage(int what) {
  		// TODO Auto-generated method stub
  		//
	  	Message msg=handler.obtainMessage(what);
	  	handler.sendMessage(msg);
  	}
    
}
