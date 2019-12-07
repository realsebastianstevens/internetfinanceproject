package com.dvyn.smss.core.di

import android.app.Application
import dagger.Component

@Component(
    modules = [
        RepositoryModule::class
    ]
)
interface ApplicationComponent {
    fun inject(app: Application)
}