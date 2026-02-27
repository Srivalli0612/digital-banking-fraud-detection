package com.bank.fraud.service;

import com.bank.fraud.dto.TransactionRequestDTO;
import com.bank.fraud.dto.TransactionResponseDTO;
import com.bank.fraud.exception.AccountNotFoundException;
import com.bank.fraud.model.Account;
import com.bank.fraud.model.FraudResult;
import com.bank.fraud.model.Transaction;
import com.bank.fraud.model.TransactionStatus;
import com.bank.fraud.repository.AccountRepository;
import com.bank.fraud.repository.FraudResultRepository;
import com.bank.fraud.repository.TransactionRepository;
import com.bank.fraud.rules.RuleBasedFraudEngine;

import java.time.LocalDateTime;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class FraudDetectionService {

    private final TransactionRepository transactionRepository;
    private final FraudResultRepository fraudResultRepository;
    private final RuleBasedFraudEngine fraudEngine;
    
    // ✅ 2.1 Logger initialized at the top
    private static final Logger log =
            LoggerFactory.getLogger(FraudDetectionService.class);

    public FraudDetectionService(TransactionRepository transactionRepository,
                                 FraudResultRepository fraudResultRepository,
                                 RuleBasedFraudEngine fraudEngine) {
        this.transactionRepository = transactionRepository;
        this.fraudResultRepository = fraudResultRepository;
        this.fraudEngine = fraudEngine;
    }

    @Autowired
    private AccountRepository accountRepository;
    
    public TransactionResponseDTO processTransaction(TransactionRequestDTO dto) {

        // ✅ Log the start of the process
        log.info("Processing transaction: {}", dto.getTransactionId());

        // ✅ Log before fetching the account
        log.info("Fetching account: {}", dto.getAccountNumber());
        Account account = accountRepository
                .findByAccountNumber(dto.getAccountNumber())
                .orElseThrow(() -> {
                    // ✅ Log the error before throwing the exception
                    log.error("Account not found: {}", dto.getAccountNumber());
                    return new AccountNotFoundException(
                            "Account not found with number: " + dto.getAccountNumber());
                });

        Transaction transaction = new Transaction();

        transaction.setTransactionId(dto.getTransactionId());
        transaction.setAccount(account);
        transaction.setAmount(dto.getAmount());
        transaction.setTransactionType(dto.getTransactionType());
        transaction.setLocation(dto.getLocation());
        transaction.setDeviceId(dto.getDeviceId());
        transaction.setMerchant(dto.getMerchant());
        transaction.setSenderName(dto.getSenderName());
        transaction.setReceiverName(dto.getReceiverName());
        transaction.setSenderAccountNumber(dto.getSenderAccountNumber());
        transaction.setReceiverAccountNumber(dto.getReceiverAccountNumber());
        transaction.setIpAddress(dto.getIpAddress());
        transaction.setStatus(TransactionStatus.valueOf(dto.getStatus()));

        // ✅ FIX ADDED HERE
        transaction.setTransactionTime(
                dto.getTransactionTime() != null 
                    ? dto.getTransactionTime()
                    : LocalDateTime.now()
            );

        Transaction savedTx = transactionRepository.save(transaction);
        
        // ✅ Log after successfully saving the transaction to the DB
        log.info("Transaction saved with ID: {}", savedTx.getTransactionId());

        FraudResult result = fraudEngine.evaluate(savedTx);

        // ✅ Final evaluation logging combined for clarity
        log.info("Fraud detected: {} | Risk Score: {}",
                result.getFraudDetected(),
                result.getRiskScore());

        savedTx.setFraudFlag(result.getFraudDetected());
        transactionRepository.save(savedTx);

        result.setTransaction(savedTx);
        fraudResultRepository.save(result);

        TransactionResponseDTO response = new TransactionResponseDTO();
        response.setTransactionId(savedTx.getTransactionId());
        response.setFraudDetected(result.getFraudDetected());
        response.setRuleTriggered(result.getRuleTriggered());
        response.setRiskScore(result.getRiskScore());
        response.setTransactionTime(savedTx.getTransactionTime());

        return response;
    }
}