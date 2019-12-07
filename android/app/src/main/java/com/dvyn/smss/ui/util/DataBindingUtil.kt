package com.dvyn.smss.ui.util

import android.view.View
import androidx.appcompat.widget.Toolbar
import androidx.databinding.BindingAdapter

object DataBindingUtil {

    @BindingAdapter("navigationClick")
    @JvmStatic
    fun setNavigationBackAction(toolbar: Toolbar, listener: View.OnClickListener) {
        toolbar.setNavigationOnClickListener(listener)
    }
}