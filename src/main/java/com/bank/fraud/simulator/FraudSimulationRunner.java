package com.bank.fraud.simulator;

import com.bank.fraud.model.Account;
import com.bank.fraud.model.AccountType;
import com.bank.fraud.model.FraudResult;
import com.bank.fraud.model.Transaction;
import com.bank.fraud.rules.RuleEngine;
import com.bank.fraud.rules.RuleEvaluationStats;

public class FraudSimulationRunner {

    public static void main(String[] args) {
        
 
    	RuleEvaluationStats stats = new RuleEvaluationStats();
        // Create dummy account
        Account account = new Account();
        account.setAccountNumber("ACC123456");
        account.setCustomerName("Test User");
        account.setAccountType(AccountType.SAVINGS);
        account.setBalance(500000.0);

        TransactionGenerator generator = new TransactionGenerator();
        RuleEngine ruleEngine = new RuleEngine();

        for (int i = 1; i <= 20; i++) {
            Transaction tx = generator.generate(account);
            FraudResult result = ruleEngine.evaluate(tx);

            stats.incrementTotal();

            if (result.getFraudDetected()) {
                stats.incrementFraud();
            } else {
                stats.incrementNormal();
            }

            System.out.println("Transaction " + i);
            System.out.println("Amount: " + tx.getAmount());
            System.out.println("Location: " + tx.getLocation());
            System.out.println("Fraud: " + result.getFraudDetected());
            System.out.println("Rule: " + result.getRuleTriggered());
            System.out.println("Merchant: " + tx.getMerchant());
            System.out.println("Time: " + tx.getTransactionTime());
            System.out.println("Risk Score: " + result.getRiskScore());
            
            System.out.println("---------------------------");
        }
        stats.printSummary();

    }
}
