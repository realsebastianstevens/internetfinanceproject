package com.dvyn.smss.core.di

import dagger.Module
import dagger.Provides
import kotlinx.coroutines.Dispatchers

@Module
class CoroutineContextProviderModule {

    @Provides
    fun provideCoroutineContext(): CoroutineContextProvider =
        CoroutineContextProvider(Dispatchers.IO)
}