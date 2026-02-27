package com.bank.fraud.controller;

import com.bank.fraud.dto.TransactionResponseDTO;
import com.bank.fraud.service.TransactionService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/transactions")
@RequiredArgsConstructor
public class TransactionController {

	
    private final TransactionService transactionService;

    @GetMapping
    public ResponseEntity<Page<TransactionResponseDTO>> getTransactions(
            @RequestParam(required = false) Boolean fraud,
            @RequestParam(required = false) String sender,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "transactionTime") String sortBy,
            @RequestParam(defaultValue = "desc") String direction
    ) {

        Page<TransactionResponseDTO> transactions =
                transactionService.getTransactions(
                        fraud, sender, page, size, sortBy, direction);

        return ResponseEntity.ok(transactions);
    }
}