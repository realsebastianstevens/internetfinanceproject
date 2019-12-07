package com.dvyn.smss.ui.screens.send

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import com.dvyn.smss.databinding.SendMoneyFragmentBinding
import com.dvyn.smss.ui.kit.BaseFragment

class SendMoneyFragment : BaseFragment() {

    lateinit var binding: SendMoneyFragmentBinding
    private lateinit var viewModel: SendMoneyViewModel

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        binding = SendMoneyFragmentBinding.inflate(inflater)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel = createViewModel(this)
        viewModel.bind(binding, this)
    }

}
