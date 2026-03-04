package com.bank.fraud.rules;

import com.bank.fraud.model.Transaction;
import com.bank.fraud.repository.TransactionRepository;
import com.bank.fraud.service.FraudRuleConfigService;

import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Component
public class MultipleFailedAttemptsRule extends BaseRule {

    private final TransactionRepository transactionRepository;

    public MultipleFailedAttemptsRule(
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

        LocalDateTime tenMinutesAgo =
                LocalDateTime.now().minusMinutes(10);

        long failedAttempts =
                transactionRepository.countRecentFailedTransactions(
                        transaction.getSenderAccountNumber(),
                        tenMinutesAgo
                );

        BigDecimal failedAttemptsBD =
                BigDecimal.valueOf(failedAttempts);

        if (failedAttemptsBD.compareTo(threshold) >= 0) {
            return riskScore();   // return rule weight
        }

        return BigDecimal.ZERO;
    }

    @Override
    public String ruleName() {
        return "MULTIPLE_FAILED_ATTEMPTS_RULE";
    }
}