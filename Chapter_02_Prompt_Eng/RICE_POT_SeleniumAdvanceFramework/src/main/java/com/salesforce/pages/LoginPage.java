package com.salesforce.pages;

import java.time.Duration;

import org.openqa.selenium.NoSuchElementException;
import org.openqa.selenium.TimeoutException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import org.openqa.selenium.support.PageFactory;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

public class LoginPage {

    private final WebDriver driver;
    private final WebDriverWait wait;

    @FindBy(xpath = "//input[@id='username']")
    private WebElement usernameField;

    @FindBy(xpath = "//input[@id='password']")
    private WebElement passwordField;

    @FindBy(xpath = "//input[@id='Login']")
    private WebElement loginButton;

    @FindBy(xpath = "//input[@id='rememberUn']")
    private WebElement rememberMeCheckbox;

    @FindBy(xpath = "//div[@id='error']")
    private WebElement loginError;

    public LoginPage(WebDriver driver) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        PageFactory.initElements(driver, this);
    }

    public void enterUsername(String username) {
        try {
            wait.until(ExpectedConditions.visibilityOf(usernameField));
            usernameField.clear();
            usernameField.sendKeys(username);
        } catch (TimeoutException e) {
            throw new AssertionError("Username field was not visible within 15 seconds", e);
        }
    }

    public void enterPassword(String password) {
        try {
            wait.until(ExpectedConditions.visibilityOf(passwordField));
            passwordField.clear();
            passwordField.sendKeys(password);
        } catch (TimeoutException e) {
            throw new AssertionError("Password field was not visible within 15 seconds", e);
        }
    }

    public void clickLogin() {
        try {
            wait.until(ExpectedConditions.elementToBeClickable(loginButton));
            loginButton.click();
        } catch (TimeoutException e) {
            throw new AssertionError("Login button was not clickable within 15 seconds", e);
        }
    }

    public void doLogin(String username, String password) {
        enterUsername(username);
        enterPassword(password);
        clickLogin();
    }

    public boolean isLoginErrorDisplayed() {
        try {
            return wait.until(ExpectedConditions.visibilityOf(loginError)).isDisplayed();
        } catch (TimeoutException e) {
            return false;
        }
    }

    public String getLoginErrorMessage() {
        try {
            return wait.until(ExpectedConditions.visibilityOf(loginError)).getText();
        } catch (TimeoutException e) {
            return "";
        }
    }

    public boolean isRememberMeDisplayed() {
        try {
            return wait.until(ExpectedConditions.visibilityOf(rememberMeCheckbox)).isDisplayed();
        } catch (TimeoutException e) {
            return false;
        }
    }

    public void selectRememberMe() {
        try {
            wait.until(ExpectedConditions.elementToBeClickable(rememberMeCheckbox));
            if (!rememberMeCheckbox.isSelected()) {
                rememberMeCheckbox.click();
            }
        } catch (TimeoutException e) {
            throw new AssertionError("Remember me checkbox was not clickable within 15 seconds", e);
        }
    }

    public boolean isRememberMeSelected() {
        try {
            return rememberMeCheckbox.isSelected();
        } catch (NoSuchElementException e) {
            throw new AssertionError("Remember me checkbox was not found", e);
        }
    }

    public String getCurrentUrl() {
        return driver.getCurrentUrl();
    }
}
