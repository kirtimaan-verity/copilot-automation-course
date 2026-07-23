import { type Locator, type Page } from '@playwright/test';

export class TaskListPage {
  readonly page: Page;
  readonly newTaskButton: Locator;
  readonly searchInput: Locator;
  readonly taskItems: Locator;
  readonly taskTitleItems: Locator;

  constructor(page: Page) {
    this.page = page;
    this.newTaskButton = page.getByTestId('new-task-btn');
    this.searchInput = page.getByTestId('search-input');
    this.taskItems = page.getByTestId('task-card');
    this.taskTitleItems = page.getByTestId('task-card-title');
  }

  async navigateTo(): Promise<void> {
    const baseUrl = process.env.BASE_URL;
    if (!baseUrl) {
      throw new Error('BASE_URL environment variable is required to navigate to /tasks');
    }

    const tasksUrl = `${baseUrl.replace(/\/+$/, '')}/tasks`;
    await this.page.goto(tasksUrl);
  }

  getTaskByTitle(title: string): Locator {
    const titleLocator = this.taskTitleItems.filter({ hasText: title });
    return this.taskItems.filter({ has: titleLocator });
  }

  async getTaskCount(): Promise<number> {
    const totalTasks = await this.taskItems.count();
    let visibleTasks = 0;

    for (let index = 0; index < totalTasks; index += 1) {
      if (await this.taskItems.nth(index).isVisible()) {
        visibleTasks += 1;
      }
    }

    return visibleTasks;
  }

  async clickNewTaskButton(): Promise<void> {
    await this.newTaskButton.click();
  }

  async searchFor(searchTerm: string): Promise<void> {
    await this.searchInput.fill(searchTerm);
  }

  async waitForTaskToAppear(title: string): Promise<void> {
    await this.getTaskByTitle(title).waitFor({ state: 'visible', timeout: 5000 });
  }
}

export default TaskListPage;