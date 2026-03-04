package com.bank.fraud;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.annotation.Bean;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.web.client.RestTemplate;

@SpringBootApplication
@EnableCaching
@EnableScheduling
@EnableJpaAuditing
public class FraudDetectionEnginedemoApplication {

    public static void main(String[] args) {
        SpringApplication.run(FraudDetectionEnginedemoApplication.class, args);
    }
    
  //Add this to allow FraudDetectionService to make HTTP requests
    @Bean 
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }   
} 
