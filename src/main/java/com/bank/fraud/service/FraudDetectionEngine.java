package com.bank.fraud.service;

import com.bank.fraud.model.Transaction;

public interface FraudDetectionEngine {

    boolean isFraud(Transaction transaction);

}
