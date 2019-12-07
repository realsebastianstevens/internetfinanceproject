package com.dvyn.smss.ui.screens.request

import androidx.lifecycle.ViewModelProviders
import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup

import com.dvyn.smss.R
import com.dvyn.smss.databinding.RequestMoneyFragmentBinding
import com.dvyn.smss.ui.kit.BaseFragment

class RequestMoneyFragment : BaseFragment() {


    private lateinit var binding: RequestMoneyFragmentBinding
    private lateinit var viewModel: RequestMoneyViewModel

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        binding = RequestMoneyFragmentBinding.inflate(inflater)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel = createViewModel(this)
        viewModel.bind(binding, this)
    }

}
