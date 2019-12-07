package com.dvyn.smss.core

import com.dvyn.smss.core.domain.Pref
import com.dvyn.smss.core.domain.Transaction
import javax.inject.Inject

class Repository @Inject constructor(val pref: Pref) {

    fun sync() {

    }

    fun fetchRecentTransactions() {

    }

    fun performTransaction(transaction: Transaction) {

    }
}