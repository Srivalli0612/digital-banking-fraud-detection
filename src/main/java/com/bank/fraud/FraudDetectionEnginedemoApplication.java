package com.bank.fraud;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class FraudDetectionEnginedemoApplication {

    public static void main(String[] args) {
        SpringApplication.run(FraudDetectionEnginedemoApplication.class, args);
    }
}
