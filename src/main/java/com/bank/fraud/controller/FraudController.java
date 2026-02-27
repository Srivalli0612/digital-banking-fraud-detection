package com.bank.fraud.controller;

import com.bank.fraud.dto.ApiResponse;
import com.bank.fraud.dto.TransactionRequestDTO;
import com.bank.fraud.dto.TransactionResponseDTO;
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
    public ResponseEntity<ApiResponse<TransactionResponseDTO>> createTransaction(
            @Valid @RequestBody TransactionRequestDTO requestDTO) {

        TransactionResponseDTO response =
                fraudDetectionService.processTransaction(requestDTO);

        ApiResponse<TransactionResponseDTO> apiResponse =
                new ApiResponse<>(
                        "SUCCESS",
                        "Transaction processed successfully",
                        response
                );

        return ResponseEntity.ok(apiResponse);
    }

    @GetMapping("/summary")
    public ResponseEntity<Map<String, Object>> getFraudSummary() {

        Map<String, Object> response = new HashMap<>();
        response.put("status", "SUCCESS");
        response.put("message", "Fraud Detection Engine is running");

        return ResponseEntity.ok(response);
    }
}
