package com.dvyn.smss.ui.screens.home

import android.widget.TextView
import androidx.databinding.BindingAdapter
import androidx.lifecycle.ViewModel
import com.dvyn.smss.R
import com.dvyn.smss.databinding.HomeFragmentBinding
import com.dvyn.smss.ui.util.findNavController
import java.text.NumberFormat
import java.util.*


class HomeViewModel : ViewModel() {
    var balance: Double = 0.0
    private lateinit var binding: HomeFragmentBinding

    fun bind(binding: HomeFragmentBinding) {
        this.binding = binding
        binding.viewModel = this
        binding.executePendingBindings()
    }

    fun sendMoney() {
        binding.findNavController().navigate(R.id.sendMoneyFragment)
    }

    fun requestMoney() {
        binding.findNavController().navigate(R.id.requestMoneyFragment)
    }

    companion object {
        @BindingAdapter("balance")
        @JvmStatic
        fun bindBalance(textView: TextView, balance: Double) {
            val format = NumberFormat.getCurrencyInstance(Locale.US)
            textView.text = format.format(balance)
        }
    }
}
