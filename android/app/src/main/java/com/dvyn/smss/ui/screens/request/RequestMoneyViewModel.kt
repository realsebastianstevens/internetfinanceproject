package com.dvyn.smss.ui.screens.request

import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModel
import com.dvyn.smss.databinding.RequestMoneyFragmentBinding
import com.dvyn.smss.ui.util.findNavController
class RequestMoneyViewModel : ViewModel() {
    private lateinit var binding: RequestMoneyFragmentBinding

    fun bind(binding: RequestMoneyFragmentBinding, fragment: Fragment) {
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
