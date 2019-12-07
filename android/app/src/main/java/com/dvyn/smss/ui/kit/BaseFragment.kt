package com.dvyn.smss.ui.kit

import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.ViewModelStoreOwner
import com.dvyn.smss.core.di.Injectable
import javax.inject.Inject


abstract class BaseFragment : Fragment(), Injectable {

    @Inject
    lateinit var viewModelFactory: ViewModelProvider.Factory

    inline fun <reified T : ViewModel> createViewModel(): T {
        return ViewModelProvider(activity!!, viewModelFactory).get(T::class.java)
    }

    inline fun <reified T : ViewModel> createViewModel(owner: ViewModelStoreOwner): T {
        return ViewModelProvider(owner, viewModelFactory).get(T::class.java)
    }
}