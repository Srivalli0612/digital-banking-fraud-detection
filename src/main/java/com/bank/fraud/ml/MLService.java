package com.bank.fraud.ml;

import com.bank.fraud.dto.MLRequestDTO;
import com.bank.fraud.dto.MLResponseDTO;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;

import org.springframework.http.*;

@Service
public class MLService {

    private final RestTemplate restTemplate = new RestTemplate();

    private final String ML_URL = "http://localhost:8000/predict";

    public BigDecimal getFraudProbability(MLRequestDTO request) {

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<MLRequestDTO> entity =
                new HttpEntity<>(request, headers);

        ResponseEntity<MLResponseDTO> response =
                restTemplate.postForEntity(
                        ML_URL,
                        entity,
                        MLResponseDTO.class
                );

        return response.getBody().getFraudProbability();
    }
}