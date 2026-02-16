package com.bank.fraud.service;

import com.bank.fraud.exception.AccountNotFoundException;
import com.bank.fraud.model.Account;
import com.bank.fraud.model.FraudResult;
import com.bank.fraud.model.Transaction;
import com.bank.fraud.repository.AccountRepository;
import com.bank.fraud.repository.FraudResultRepository;
import com.bank.fraud.repository.TransactionRepository;
import com.bank.fraud.rules.RuleBasedFraudEngine;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class FraudDetectionService {

    private final TransactionRepository transactionRepository;
    private final FraudResultRepository fraudResultRepository;
    private final RuleBasedFraudEngine fraudEngine;

    public FraudDetectionService(TransactionRepository transactionRepository,
                                 FraudResultRepository fraudResultRepository,
                                 RuleBasedFraudEngine fraudEngine) {
        this.transactionRepository = transactionRepository;
        this.fraudResultRepository = fraudResultRepository;
        this.fraudEngine = fraudEngine;
    }

    @Autowired
    private AccountRepository accountRepository;
    
    public FraudResult processTransaction(Transaction transaction) {
        
    	Long accountId = transaction.getAccount().getId();

        Account account = accountRepository.findById(accountId)
                .orElseThrow(() ->
                        new AccountNotFoundException("Account not found with ID: " + accountId));

        transaction.setAccount(account);
    	
        // First save to trigger @PrePersist
        Transaction savedTx = transactionRepository.save(transaction);
         
        // Now evaluate (transactionTime is available)
        FraudResult result = fraudEngine.evaluate(savedTx);
        
        // Set fraud flag inside transaction
        savedTx.setFraudFlag(result.getFraudDetected());
        transactionRepository.save(savedTx);
        
        result.setTransaction(savedTx);

        // Save fraud result
        return fraudResultRepository.save(result);
    }
}
