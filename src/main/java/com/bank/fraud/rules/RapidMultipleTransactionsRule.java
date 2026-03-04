package com.bank.fraud.rules;

import com.bank.fraud.model.Transaction;
import com.bank.fraud.repository.FraudRuleConfigRepository;
import com.bank.fraud.repository.TransactionRepository;
import com.bank.fraud.service.FraudRuleConfigService;

import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Component
public class RapidMultipleTransactionsRule extends BaseRule {

    private final TransactionRepository transactionRepository;

    public RapidMultipleTransactionsRule(
    		FraudRuleConfigService configService,
            TransactionRepository transactionRepository) {
        super(configService);
        this.transactionRepository = transactionRepository;
    }

    @Override
    public BigDecimal evaluate(Transaction transaction) {

        if (!isActive()) return BigDecimal.ZERO;

        BigDecimal threshold = getThreshold();
        if (threshold == null) return BigDecimal.ZERO;

        LocalDateTime fiveMinutesAgo =
                LocalDateTime.now().minusMinutes(5);

        long recentCount =
                transactionRepository.countRecentTransactions(
                        transaction.getSenderAccountNumber(),
                        fiveMinutesAgo
                );

        BigDecimal recentCountBD =
                BigDecimal.valueOf(recentCount);

        if (recentCountBD.compareTo(threshold) > 0) {
            return riskScore();   // return rule weight
        }

        return BigDecimal.ZERO;
    }

    @Override
    public String ruleName() {
        return "RAPID_MULTIPLE_TRANSACTIONS_RULE";
    }
}