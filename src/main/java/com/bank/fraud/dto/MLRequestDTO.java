package com.bank.fraud.dto;

import java.math.BigDecimal;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MLRequestDTO { 

    private BigDecimal amount;
    private int hour;
    private int locationRisk;
    private int velocityScore;

    // getters & setters
}
