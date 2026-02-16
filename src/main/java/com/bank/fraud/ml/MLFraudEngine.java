package com.bank.fraud.ml;

import org.springframework.stereotype.Component;

import com.bank.fraud.model.Transaction;
import com.bank.fraud.service.FraudDetectionEngine;

@Component
//@Primary   // switches engine without code change
public class MLFraudEngine implements FraudDetectionEngine {

    @Override
    public boolean isFraud(Transaction transaction) {

        // Call ML model here
        // Python REST API / TensorFlow / PMML / ONNX

        return false;
    }

}
