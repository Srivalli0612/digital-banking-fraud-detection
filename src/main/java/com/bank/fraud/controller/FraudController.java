package com.bank.fraud.controller;

import com.bank.fraud.model.FraudResult;
import com.bank.fraud.model.Transaction;
import com.bank.fraud.service.FraudDetectionService;

import jakarta.validation.Valid;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/fraud")
public class FraudController {

    @Autowired
    private FraudDetectionService fraudDetectionService;

    @PostMapping("/transactions")
    public ResponseEntity<FraudResult> createTransaction(@Valid @RequestBody Transaction transaction) {

        FraudResult result = fraudDetectionService.processTransaction(transaction);

        return ResponseEntity.ok(result);
    }

    @GetMapping("/summary")
    public ResponseEntity<Map<String, Object>> getFraudSummary() {

        Map<String, Object> response = new HashMap<>();
        response.put("status", "SUCCESS");
        response.put("message", "Fraud Detection Engine is running");

        return ResponseEntity.ok(response);
    }
}
