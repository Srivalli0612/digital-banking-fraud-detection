package com.bank.fraud.repository;

import com.bank.fraud.model.FraudResult;
import org.springframework.data.jpa.repository.JpaRepository;

public interface FraudResultRepository extends JpaRepository<FraudResult, Long> {
}
