package com.rh.activity;

import com.rh.activity.WelcomeView;
import com.rh.activity.R;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.util.DisplayMetrics;
import android.view.SurfaceHolder;
import android.view.SurfaceView;

/**
 * @Title:		
 * @Fution:		
 * @Author: 	rh_Jameson
 * @date:		2014/10/24
 */

/*
 *SurfaceHolder: surfacesurface
 *SurfaceHolder.Callback: 	surfaceChanged + surfaceCreated + surfaceDestroyed
 */
public class WelcomeView extends SurfaceView implements SurfaceHolder.Callback{
	//
	MainActivity mainActivity;
	
	// 
	
	//j
	int currentAlpha=0;		
	
	//
	Bitmap backgroundImg;
	//
	int screenWidth;
	int screenHeight;	
	int sleepSpan=60;//ms
	
	// 
	Paint paint;
	
	//j
	int currentX;
	int currentY;
	
	public WelcomeView(Context context) {
		super(context);
	}
	//View
	public WelcomeView(MainActivity mainActivity) {
		super(mainActivity);
		// TODO Auto-generated constructor stub
		this.mainActivity=mainActivity;
		
		//L
		DisplayMetrics dm = getResources().getDisplayMetrics();
        screenWidth = dm.widthPixels;
        screenHeight = dm.heightPixels;
        //System.out.println(screenHeight+","+screenWidth);
		
        //n
        backgroundImg=BitmapFactory.decodeResource(mainActivity.getResources(), R.drawable.client_welcome_ui);
				
		paint=new Paint();

		//surfaceViewsurface,SurfaceViewj
		this.getHolder().addCallback(this);
	}
	
	public void Draw(Canvas canvas){	
		//
		paint.setColor(Color.BLACK);//u
		paint.setAlpha(255);
		canvas.drawRect(0, 0, screenWidth, screenHeight, paint);
		
		//
		if(backgroundImg==null)return;
		paint.setAlpha(currentAlpha);		
		canvas.drawBitmap(backgroundImg, currentX, currentY, paint);	
	}
	
	

	@Override
	public void surfaceChanged(SurfaceHolder holder, int format, int width,
			int height) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void surfaceCreated(SurfaceHolder holder) {
		// TODO Auto-generated method stub
		new Thread()
		{
	
			@Override
			public void run() {
				// TODO Auto-generated method stub
					
				//
				currentX=screenWidth/2-backgroundImg.getWidth()/2;
				currentY=screenHeight/2-backgroundImg.getHeight()/2;
				
				for(int i=255;i>-20;i=i-20)
				{//	
					currentAlpha=i;
					if(currentAlpha<0)
					{
						currentAlpha=0;
					}
					SurfaceHolder myholder=WelcomeView.this.getHolder();
					Canvas canvas = myholder.lockCanvas();//
					try{
						synchronized(myholder){
							Draw(canvas);//
						}
					}
					catch(Exception e){
						e.printStackTrace();
					}
					finally{
						if(canvas != null){
							myholder.unlockCanvasAndPost(canvas);
						}
					}						
					try
					{
						if(i==255)
						{//
							Thread.sleep(1000);
						}
						Thread.sleep(sleepSpan);
					}
					catch(Exception e)
					{
						e.printStackTrace();
					}
				}	
				
				//
				mainActivity.sendMessage(WhatMessage.gotoLoginActivity);
			}
		
		
		}.start();
	}

	@Override
	public void surfaceDestroyed(SurfaceHolder holder) {
		// TODO Auto-generated method stub
		
	}

}
