package com.dvyn.smss.core.di

import android.app.Application
import android.content.Context
import com.dvyn.smss.core.domain.Pref
import dagger.Module
import dagger.Provides

@Module
class ApplicationModule(private val application: Application) {

    @Provides
    fun provideContext(): Context = application.applicationContext

    @Provides
    fun providePref() = Pref(application)
}