package com.dvyn.smss.core.di

import dagger.Module

@Module(includes = [ApplicationModule::class, CoroutineContextProviderModule::class, DatabaseModule::class])
class RepositoryModule