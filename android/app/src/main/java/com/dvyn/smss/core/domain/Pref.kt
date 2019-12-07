package com.dvyn.smss.core.domain

import android.content.Context
import androidx.preference.PreferenceManager

class Pref(context: Context) {
    private val context: Context = context.applicationContext
    private val pref = PreferenceManager.getDefaultSharedPreferences(this.context)

    var publicKey: String?
        get() {
            return pref.getString(PUBLIC_KEY, null)
        }
        set(value) {
            pref.edit().putString(PUBLIC_KEY, value).apply()
        }

    var privateKey: String?
        get() {
            return pref.getString(PRIVATE_KEY, null)
        }
        set(value) {
            pref.edit().putString(PRIVATE_KEY, value).apply()
        }

    var balance: Double
        get() {
            return pref.getFloat(BALANCE, 0.0F).toDouble()
        }
        set(value) {
            pref.edit().putFloat(BALANCE, value.toFloat()).apply()
        }

    companion object {
        const val PRIVATE_KEY = "PRIVATE_KEY"
        const val PUBLIC_KEY = "PUBLIC_KEY"
        const val BALANCE = "BALANCE"
    }
}