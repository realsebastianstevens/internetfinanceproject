package com.dvyn.smss.ui.util

import androidx.navigation.NavController
import androidx.navigation.findNavController
import androidx.viewbinding.ViewBinding

fun ViewBinding.findNavController(): NavController {
    return root.findNavController()
}