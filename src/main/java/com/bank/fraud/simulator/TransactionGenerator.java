package com.bank.fraud.simulator;

import com.bank.fraud.model.*;
import com.github.javafaker.Faker;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Random;
import java.util.UUID;

public class TransactionGenerator {

    private final Random random = new Random();

    private final String[] locations = {
            "INDIA", "USA", "UK", "GERMANY",
            "KOLKATA", "DELHI", "MUMBAI", 
            "BANGALORE", "CHENNAI", 
            "HYDERABAD", "PATNA"
    };

    private final String[] merchants = {
            "AMAZON", "FLIPKART", 
            "SCAM_PAY", "DARKWEB_STORE"
    };

    private final String[] ips = {
            "192.168.1.10",
            "10.0.0.66",       // suspicious
            "172.16.0.5"
    };

    public Transaction generate(Account account) {

        Transaction tx = new Transaction();
        Faker faker = new Faker();

        tx.setTransactionId(UUID.randomUUID().toString());
        tx.setAccount(account);

        tx.setAmount(generateAmount());  // ✅ BigDecimal now

        tx.setTransactionType(randomTransactionType());
        tx.setLocation(randomLocation());
        tx.setDeviceId("DEVICE-" + random.nextInt(1000));
        tx.setMerchant(randomMerchant());

        tx.setSenderName(faker.name().fullName());
        tx.setReceiverName(faker.name().fullName());

        tx.setSenderAccountNumber(account.getAccountNumber());
        tx.setReceiverAccountNumber("ACC" + (100000 + random.nextInt(999999)));

        tx.setIpAddress(randomIP());
        tx.setStatus(randomStatus());

        tx.setFraudFlag(false);
        tx.setTransactionTime(LocalDateTime.now());

        return tx;
    }

    private BigDecimal generateAmount() {

        // 10% chance high value transaction
        if (random.nextInt(10) == 0) {
            return BigDecimal.valueOf(
                    200000 + random.nextInt(300000)
            );
        }

        return BigDecimal.valueOf(
                500 + random.nextInt(20000)
        );
    }

    private String randomTransactionType() {
        String[] types = {"ATM", "ONLINE", "POS"};
        return types[random.nextInt(types.length)];
    }

    private String randomLocation() {
        return locations[random.nextInt(locations.length)];
    }

    private String randomMerchant() {
        return merchants[random.nextInt(merchants.length)];
    }

    private String randomIP() {
        return ips[random.nextInt(ips.length)];
    }

    private TransactionStatus randomStatus() {

        // 20% failure chance
        if (random.nextInt(5) == 0) {
            return TransactionStatus.FAILED;
        }

        return TransactionStatus.SUCCESS;
    }
}