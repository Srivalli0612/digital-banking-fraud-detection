package com.bank.fraud.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "accounts")
public class Account {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    @NotBlank(message = "Account number is required")
    private String accountNumber;

    @Column(nullable = false)
    @NotBlank(message = "Customer name is required")
    private String customerName;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    @NotNull(message = "Account type is required")
    private AccountType accountType;

    @Column(nullable = false)
    @NotNull(message = "Balance cannot be null")
    @PositiveOrZero(message = "Balance cannot be negative")
    private Double balance;

    @Column(nullable = false)
    private Boolean active = true;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    // -------- Lifecycle Method --------
    @PrePersist
    public void prePersist() {
        createdAt = LocalDateTime.now();
    }

    // -------- Constructors --------
    public Account() {
    }

    // -------- Getters & Setters --------
    public Long getId() {
        return id;
    }

    public String getAccountNumber() {
        return accountNumber;
    }

    public void setAccountNumber(String accountNumber) {
        this.accountNumber = accountNumber;
    }

    public String getCustomerName() {
        return customerName;
    }

    public void setCustomerName(String customerName) {
        this.customerName = customerName;
    }

    public AccountType getAccountType() {
        return accountType;
    }

    public void setAccountType(AccountType accountType) {
        this.accountType = accountType;
    }

    public Double getBalance() {
        return balance;
    }

    public void setBalance(Double balance) {
        this.balance = balance;
    }

    public Boolean getActive() {
        return active;
    }

    public void setActive(Boolean active) {
        this.active = active;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
}
