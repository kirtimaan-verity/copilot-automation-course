import { type Locator, type Page } from '@playwright/test';

export default class TaskFormPage {
  readonly page: Page;
  readonly form: Locator;
  readonly titleInput: Locator;
  readonly descriptionInput: Locator;
  readonly dueDateInput: Locator;
  readonly prioritySelect: Locator;
  readonly submitButton: Locator;
  readonly cancelButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.form = page.getByTestId('task-form');
    this.titleInput = page.getByTestId('task-title');
    this.descriptionInput = page.getByTestId('task-description');
    this.dueDateInput = page.getByTestId('task-due-date');
    this.prioritySelect = page.getByTestId('task-priority');
    this.submitButton = page.getByTestId('submit-btn');
    this.cancelButton = page.getByTestId('cancel-btn');
    this.errorMessage = page.getByTestId('error-message');
  }

  async fillTitle(title: string): Promise<void> {
    await this.titleInput.fill(title);
  }

  async fillDescription(description: string): Promise<void> {
    await this.descriptionInput.fill(description);
  }

  async setDueDate(date: string): Promise<void> {
    await this.dueDateInput.fill(date);
  }

  async setPriority(priority: 'Low' | 'Medium' | 'High'): Promise<void> {
    const valueMap: Record<'Low' | 'Medium' | 'High', 'low' | 'medium' | 'high'> = {
      Low: 'low',
      Medium: 'medium',
      High: 'high',
    };
    await this.prioritySelect.selectOption(valueMap[priority]);
  }

  async submit(): Promise<void> {
    await this.submitButton.click();
  }

  async cancel(): Promise<void> {
    await this.cancelButton.click();
  }

  async getErrorMessage(): Promise<string> {
    const message = await this.errorMessage.textContent();
    return (message ?? '').trim();
  }
}