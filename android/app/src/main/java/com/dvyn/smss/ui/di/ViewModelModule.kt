package com.dvyn.smss.ui.di

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.dvyn.smss.ui.screens.home.HomeViewModel
import com.dvyn.smss.ui.screens.request.RequestMoneyViewModel
import com.dvyn.smss.ui.screens.send.SendMoneyViewModel
import dagger.Binds
import dagger.Module
import dagger.multibindings.IntoMap

@Suppress("unused")
@Module
abstract class ViewModelModule {

    @Binds
    abstract fun bindViewModelFactory(factory: ViewModelFactory): ViewModelProvider.Factory

    @Binds
    @IntoMap
    @ViewModelKey(HomeViewModel::class)
    abstract fun bindHomeViewModel(vm: HomeViewModel): ViewModel

    @Binds
    @IntoMap
    @ViewModelKey(SendMoneyViewModel::class)
    abstract fun bindSendMoneyViewModel(vm: SendMoneyViewModel): ViewModel


    @Binds
    @IntoMap
    @ViewModelKey(RequestMoneyViewModel::class)
    abstract fun bindRequestMoneyViewModel(vm: RequestMoneyViewModel): ViewModel
}
