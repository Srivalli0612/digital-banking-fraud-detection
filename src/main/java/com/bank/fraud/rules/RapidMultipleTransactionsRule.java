package com.bank.fraud.rules;

import com.bank.fraud.model.Transaction;
import com.bank.fraud.repository.TransactionRepository;

import java.time.LocalDateTime;
import java.util.List;

import org.springframework.stereotype.Component;

@Component
public class RapidMultipleTransactionsRule implements FraudRule {

	 private final TransactionRepository transactionRepository;

	    public RapidMultipleTransactionsRule(TransactionRepository transactionRepository) {
	        this.transactionRepository = transactionRepository;
	    }
	    
	    
    @Override
    public boolean evaluate(Transaction transaction) {

        if (transaction.getTransactionTime() == null) {
            return false;
        }

    
        LocalDateTime oneMinuteAgo =
                transaction.getTransactionTime().minusMinutes(1);

        List<Transaction> recentTransactions =
                transactionRepository.findByAccountIdAndTransactionTimeAfter(
                        transaction.getAccount().getId(),
                        oneMinuteAgo
                );

        return recentTransactions.size() >= 3; // 3+ transactions within 1 minute
    }

    @Override
    public String ruleName() {
        return "RAPID_MULTIPLE_TX_RULE";
    }

    @Override
    public double riskScore() {
        return 0.9;
    }
}
