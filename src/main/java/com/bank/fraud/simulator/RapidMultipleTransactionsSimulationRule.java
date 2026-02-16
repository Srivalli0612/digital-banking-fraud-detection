package com.bank.fraud.simulator;

import com.bank.fraud.model.Transaction;
import com.bank.fraud.rules.FraudRule;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

public class RapidMultipleTransactionsSimulationRule implements FraudRule {

    private static final List<Transaction> transactionHistory = new ArrayList<>();

    @Override
    public boolean evaluate(Transaction transaction) {

        if (transaction.getTransactionTime() == null) {
            return false;
        }

        int count = 0;

        for (Transaction pastTx : transactionHistory) {

            if (pastTx.getAccount().getAccountNumber()
                    .equals(transaction.getAccount().getAccountNumber())) {

                long seconds = Duration.between(
                        pastTx.getTransactionTime(),
                        transaction.getTransactionTime()
                ).getSeconds();

                if (seconds >= 0 && seconds <= 60) {
                    count++;
                }
            }
        }

        transactionHistory.add(transaction);

        return count >= 3; // 3 transactions within 1 minute
    }

    @Override
    public String ruleName() {
        return "RAPID_MULTIPLE_SIMULATION_RULE";
    }

    @Override
    public double riskScore() {
        return 0.9;
    }
}
