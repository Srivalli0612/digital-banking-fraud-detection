package com.bank.fraud.simulator;

import com.bank.fraud.model.Account;
import com.bank.fraud.model.Transaction;

import java.time.LocalDateTime;
import java.util.Random;
import java.util.UUID;

public class TransactionGenerator {

    private static final String[] LOCATIONS = {"INDIA", "USA", "UK", "GERMANY"};
    private static final String[] TYPES = {"ATM", "ONLINE", "POS"};
    private static final String[] MERCHANTS = {
            "AMAZON", "FLIPKART", "PAYTM",
            "SCAM_PAY", "DARKWEB_STORE"
    };

    private final Random random = new Random();

    // Keep last transaction time for rapid simulation
    private LocalDateTime lastTransactionTime = LocalDateTime.now();

    public Transaction generate(Account account) {

        Transaction transaction = new Transaction();

        transaction.setTransactionId(UUID.randomUUID().toString());
        transaction.setAccount(account);

        transaction.setAmount(generateAmount());
        transaction.setLocation(randomLocation());
        transaction.setTransactionType(randomType());
        transaction.setDeviceId("DEV-" + random.nextInt(1000));

        //  Set merchant
        transaction.setMerchant(randomMerchant());

        // Set transaction time manually (since @PrePersist won't run)
        transaction.setTransactionTime(generateTransactionTime());

        return transaction;
    }

    private double generateAmount() {
        // 10% chance of high suspicious spike
        if (random.nextInt(10) == 0) {
            return 150000 + random.nextInt(50000);
        }
        return 1000 + random.nextInt(20000);
    }

    private String randomLocation() {
        return LOCATIONS[random.nextInt(LOCATIONS.length)];
    }

    private String randomType() {
        return TYPES[random.nextInt(TYPES.length)];
    }

    private String randomMerchant() {
        return MERCHANTS[random.nextInt(MERCHANTS.length)];
    }

    private LocalDateTime generateTransactionTime() {

        // 30% chance of rapid transaction (within 30 seconds)
        if (random.nextInt(10) < 3) {
            lastTransactionTime = lastTransactionTime.plusSeconds(random.nextInt(30));
        } else {
            // Otherwise spread out transactions
            lastTransactionTime = lastTransactionTime.plusMinutes(5);
        }

        // 20% chance of odd hour fraud (between 12 AM – 5 AM)
        if (random.nextInt(10) < 2) {
            return lastTransactionTime.withHour(random.nextInt(5));
        }

        return lastTransactionTime;
    }
}
