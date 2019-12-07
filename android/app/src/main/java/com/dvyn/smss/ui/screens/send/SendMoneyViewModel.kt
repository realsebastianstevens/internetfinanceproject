package com.dvyn.smss.ui.screens.send

import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModel
import com.dvyn.smss.databinding.SendMoneyFragmentBinding
import com.dvyn.smss.ui.util.findNavController

class SendMoneyViewModel : ViewModel() {
    private lateinit var binding: SendMoneyFragmentBinding

    fun bind(binding: SendMoneyFragmentBinding, fragment: Fragment) {
        this.binding = binding
//        val activity = fragment.activity as AppCompatActivity
//        activity.setSupportActionBar(binding.toolbar)
        binding.viewModel = this
        binding.executePendingBindings()
    }

    fun goBack() {
        binding.findNavController().popBackStack()
    }
}
